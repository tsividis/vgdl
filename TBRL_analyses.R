setwd('/Users/pedrotsividis/Projects/atari/vgdl')

## Load helper functions
source(paste(getwd(), '/TBRL_functions.R', sep=''))

EMPA_dates = list('mar28')
lesion_dates = list('jun3', 'jun22', 'jun23')
dqn_path = paste(getwd(),'/data_files/ddqn', sep='')
rainbow_path = paste(getwd(),'/data_files/rainbow', sep='')
random_path = paste(getwd(),'/data_files/randomdata', sep='')
humandatapaths = list.files(paste(getwd(),'/data_files/humandata', sep=''))

## Load data. These next few lines take a long time.
humandata = load_reward_data('human', NA)
EMPAdata = load_reward_data('EMPA', EMPA_dates)
EMPA_variants = filter(EMPAdata, agent_type!='EMPA')
new_lesions = load_reward_data('EMPA', c('apr4', 'jun3', 'jun22', 'jun23')) ## TODO: rename
dqndata = load_reward_data('DDQN', NA)
rainbowdata = load_reward_data('rainbow', NA)
# randomdata = load_reward_data('random', NA)

##Load subjective game ratings
ratings = load_ratings()

## Remove subject-game pairs where the subject said they'd played the game before.
played_before = filter(ratings, played.before=='Yes')
for (game in unique(played_before$gameName)){
  for (subject in unique(filter(played_before, gameName==game)$subject)){
    humandata = filter(humandata, !((game_name==game) & (subject_ID==subject)))
  }
}

## Find all (subject, game, level) tuples where the subject was forced to play a level more than once.
## (this is slow)
excluded_subjects = data.frame(game_name=as.character(), subject_ID=as.character(), level=as.numeric())
for (game in unique(humandata$game_name)){
  human_game_data = filter(humandata, game_name==game)
  for (subject in unique(humandata$subject_ID)){
    subject_data = filter(humandata, subject_ID==subject)
    for (level in unique(subject_data$level_number)){
      if (length(unique(filter(subject_data, level_number==level)$cumulative_wins))>2){
        excluded_subjects = rbind(excluded_subjects, data.frame(game_name=game, subject_ID=subject, level_number=level))
      }
    }
  }
}
## Remove game-subject pairs where the subject played a given level in a game more than once 
## (this only happened a few times)
for (i in 1:length(excluded_subjects$game_name)){
  row = excluded_subjects[i,]
  game = row$game_name
  subject = row$subject_ID
  humandata = filter(humandata, !((game_name==as.character(game))&(subject_ID==as.character(subject))))
}


## Grab first 5 of each lesion.
first_5_IDs_of_each_lesion_type = rep(NA, 9*450)
i = 1
for (agent in unique(new_lesions$agent_type)){
  if (!(agent %in% c('e-greedy 1k SN', 'e-greedy 1k SS', 'EMPA'))){
    agent_data = filter(new_lesions, agent_type==agent)
    for (game in unique(agent_data$game)){
      game_data = filter(agent_data, game_name==game)
      for (subject in unique(game_data$subject_ID)[1:5]){
        first_5_IDs_of_each_lesion_type[i] = subject
        print(i)
        i = i+1
      }
    }
  }
}
new_lesions = filter(new_lesions, subject_ID%in%first_5_IDs_of_each_lesion_type)

alldata = rbind(humandata, EMPAdata, new_lesions, dqndata, rainbowdata)
human_normed_data = make_human_normed_data(alldata)


## Global plot styling
removeGrid(x = TRUE, y = TRUE)

colors = c('steelblue1', 'slategray2',
           'slateblue1', 'slateblue4', 'mediumpurple1', 'purple1',
           'firebrick2', 'magenta3',
           'palegreen3',
           'gray50', 'gray65', 'gray80',
           'orange3', 'tomato3', 'red3', 'red3',
           'goldenrod1', 'goldenrod2', 'goldenrod3', 'darkslategray2', 'darkolivegreen3')
names(colors)=c('EMPA', 'EMPA fail',
                'e-greedy 1k', 'e-greedy 2k', 'e-greedy 1k DS', 'e-greedy 2k DS',
                'random policy', 'random',
                'human',
                'DDQN 100k', 'DDQN 10k', 'DDQN 1k',
                'rainbow 250k', 'rainbow 150k', 'rainbow 50k', 'rainbow',
                'no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW', 'no subgoals + no gradient + no IW')


### Learning curve plots
## plotting all agents/models
games_to_plot = c('bait', 'zelda', 'butterflies', 'avoidgeorge','frogs','plaqueattack')
games_in_order = unique(alldata$game_name)[order(unique(alldata$game_name))]
plots = list()
for (k in 1:length(games_to_plot)){
# for (k in 1:length(games_in_order)){
  agents_to_plot = c('human', 'rainbow 150k', 'DDQN 100k', 'EMPA')
  # game = games_in_order[k]
  game = games_to_plot[k]

  max_x = 1000000
  
  ## used for adding data points to sparse DDQN data
  if(max_x<5000){
    step_size=5
  }else if(max_x<100000){
    step_size=100
  }else if(max_x<1000000){
    step_size=1000
  }else{
    step_size=10000
  }
  
  d = filter(alldata, game_name==game, agent_type %in% agents_to_plot)
  ### assign correct colors to each subject ID
  plotcolors = c()
  for (agent in agents_to_plot){
    agent_subjects = unique(filter(d, agent_type==agent)$subject_ID)
    agent_color = colors[agent]
    colorlist = rep(agent_color, length(agent_subjects))
    names(colorlist) = agent_subjects
    plotcolors = c(plotcolors, colorlist)
  }
  
  if (game%in%levels(excluded_subjects)){
    es = filter(excluded_subjects, game_name==game)
    subjects_to_exclude = unique(es$subject_ID)
  }else{
    subjects_to_exclude = c()
  }

  d = filter(d, !(subject_ID%in%subjects_to_exclude))


  if (game %in% c('antagonist', 'antagonist_1', 'antagonist_2', 'bees_and_birds', 'bees_and_birds_1', 
                  'closing_gates', 'closing_gates_1', 'corridor', 'corridor_1', 
                  'helper', 'helper_1', 'helper_2', 'preconditions', 'preconditions_1', 'preconditions_2',
                  'push_boulders', 'push_boulders_1', 'push_boulders_2', 'relational', 'relational_1', 'relational_2',
                  'surprise', 'surprise_1', 'surprise_2')){
    level_max = 4
  }else if (game %in% c('ee', 'ee_1', 'ee_2', 'ee_3')){
    level_max = 6
  }else{
    level_max = 5
  }
  ## Add data points for every 'step_size' DDQN time-step, since we can afford to do this and know what the data points are
  ## (as we recorded end-of-episode data and cumulative_wins definitionally don't change before then)
  ## WARNING: if you ever plotted score, you wouldn't be able to do this. You didn't record score within episodes for DDQN.
  if (max_x<1000000){
  replacement_subjects = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                              modelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
  clean_d=filter(d, (!grepl('DDQN', agent_type) & (!grepl('rainbow', agent_type))) )
  for (subject in unique(filter(d, (grepl('DDQN', agent_type)|(grepl('rainbow', agent_type))))$subject_ID)){
    subject_data = filter(d, subject_ID==subject, cumulative_steps<max_x)
    
    ## if we actually have subject data for the max_x cutoff we care about...
    if (length(subject_data$cumulative_steps)>0){
      subject_agent_type = subject_data$agent_type[1]
      last_steps = 0
      
      new_subject_df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                                  modelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
      
      for (i in 1:length(subject_data$cumulative_steps)){ ## meaning, for each episode
        subject_row = subject_data[i,]
        if ( (last_steps<subject_row$cumulative_steps)){
          if (subject_row$cumulative_wins<level_max){## add lots of points if game is not won
            for (j in seq(last_steps, subject_row$cumulative_steps-1,step_size)){
                    row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                           modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                           score=subject_row$score)
            new_subject_df = rbind(new_subject_df, row)
            }
          }
          else{ ## just add the last row
              row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                               modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                               score=subject_row$score)
              new_subject_df = rbind(new_subject_df, row)    
            }
        new_subject_df = rbind(new_subject_df, subject_row)
        last_steps = subject_row$cumulative_steps
        }
      }
      ## If we haven't filled out the x range
      last_x = new_subject_df$cumulative_steps[length(new_subject_df$cumulative_steps)]
      if(last_x+step_size<max_x){
        subject_row = new_subject_df[length(new_subject_df$cumulative_steps),]
        for (j in seq(last_x+step_size, max_x, step_size)){
          row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                           modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                           score=subject_row$score)
          new_subject_df = rbind(new_subject_df, row)
        }
      }
      replacement_subjects = rbind(replacement_subjects, new_subject_df)
    } 
    
    clean_d = rbind(clean_d, replacement_subjects) 
  }
  d = clean_d
  }
  
  d = filter(d, cumulative_steps<=max_x)
  
  ## you can only assume DDQN kept playing for max_x steps. Humans might have quit before then, and EMPA might be stuck thinking, within the allotted limit.
  no_win_subjects = c()
  for (subject in unique(d$subject_ID)){
    if (max(filter(d, subject_ID==subject, cumulative_steps<=max_x)$cumulative_wins)==0){
      no_win_subjects = c(no_win_subjects, subject)
    }
  }
  
  ### calculate kappas here:
  kappa_df = data.frame(agent_type=as.character, efficiency=as.numeric())
  for (agent in unique(d$agent_type)){
    agent_data = filter(d, agent_type==agent)
    
    level_maxes = list()
    cumulative_step_maxes = list()
    idx=1
    for (l in 1:length(unique(agent_data$subject_ID))){
      subject = unique(agent_data$subject_ID)[l]
      subjectdata = filter(agent_data, subject_ID==subject)
      if (length(subjectdata$cumulative_steps)>0){
        if(max(subjectdata$cumulative_steps)>0){
          level_maxes[[idx]] = max(subjectdata$cumulative_wins)
          cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
          idx = idx+1            
        }
      }
    }
    
    ## mean vector of win numbers
    mean_wins = mean(as.numeric(as.vector(level_maxes)))
    
    ##mean of vector steps+to+win ratios (kappa)
    l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
    kappa_df = rbind(kappa_df, data.frame(agent_type=agent, efficiency=l_e))
  }
  
  d=transform(d, subject_ID=factor(subject_ID, levels=names(plotcolors))) ## reorder in order to plot EMPA on top, as it otherwise can get lost in the many human curves.
  max_y = level_max
  
  game_title=gsub('_',' ',game)
  if (game_title=='ee'){
    game_title='explore/exploit'
  }
  if (game_title=='ee 1'){
    game_title='explore/exploit 1'
  }
  if (game_title=='ee 2'){
    game_title='explore/exploit 2'
  }
  if (game_title=='ee 3'){
    game_title='explore/exploit 3'
  }
  p = ggplot(d ,aes(x=cumulative_steps,y=cumulative_wins, color=subject_ID, size=agent_type))+geom_point()+ 
    ggtitle(game_title)+theme(legend.position="none")+scale_color_manual(values=plotcolors)+scale_size_manual(values=c(1,1,1,1))+
    xlab('Steps taken by agent')+ylab('Levels won')+
    theme(plot.title=element_text(family='',face='plain', size=26, hjust=0.5),
          axis.text.x=element_text(size=22),
          axis.text.y=element_text(size=22),
          axis.title.x=element_text(size=24),
          axis.title.y=element_text(size=24),
          panel.background = element_blank())
  
  p=p+geom_smooth(data=filter(d,!(subject_ID%in%no_win_subjects)), se=FALSE)
  if ( (length(no_win_subjects)>0) & length(filter(d,subject_ID%in%no_win_subjects,grepl('DDQN', agent_type))$cumulative_steps>0) ){
    p = p+geom_segment(aes(x=0,y=0,xend=max_x,yend=0),data=filter(d,subject_ID%in%no_win_subjects,grepl('DDQN', agent_type)),size=1.4)
  }
  if ( (length(no_win_subjects)>0) & length(filter(d,subject_ID%in%no_win_subjects,grepl('rainbow', agent_type))$cumulative_steps>0) ){
    p = p+geom_segment(aes(x=0,y=0.05,xend=max_x,yend=0.05),data=filter(d,subject_ID%in%no_win_subjects,grepl('rainbow', agent_type)),size=1.4)
  }
  ## there are some games where you got 0 DDQN data in short ranges of time, like 1k steps for chase.
  if (length(filter(d, grepl('DDQN', agent_type), cumulative_steps<max_x)$cumulative_steps)==0){
    p = p+geom_segment(aes(x=0,y=0,xend=max_x,yend=0,alpha=.7),data=d,size=1.4, color=colors['DDQN 100k'])
  }
  if (length(filter(d, grepl('rainbow', agent_type), cumulative_steps<max_x)$cumulative_steps)==0){
    p = p+geom_segment(aes(x=0,y=0.05,xend=max_x,yend=0.05,alpha=.7),data=d,size=1.4, color=colors['rainbow']) ## add offset so that it's visible w/ DDQN.
  }
  
  p=p+xlim(0,max_x)+ylim(0,max_y)

  if(max_x==10000){
    p=p+scale_x_continuous(breaks=c(0, 2500, 5000, 7500, 10000),labels=c('0', '2.5k', '5k', '7.5k', '10k'), limits=c(0,10000))
  }  
  if(max_x==1000000){
    p=p+scale_x_continuous(breaks=c(0, 250000, 500000, 750000, 1000000),labels=c('0', '250k', '500k', '750k', '1mil'), limits=c(0,1000000))
  }

  human_kappa = filter(kappa_df, agent_type=='human')$efficiency
  EMPA_kappa = filter(kappa_df, agent_type=='EMPA')$efficiency
  DDQN_kappa = filter(kappa_df, agent_type=='DDQN 100k')$efficiency
  kappa_string = paste('Learning efficiency (\u03ba):','\nHuman: ', human_kappa, '\nEMPA: ', 
                       EMPA_kappa, '\nDDQN: ', 
                       DDQN_kappa, sep='')
  # p=p+annotate("label", x = max_x*.25, y = max_y*.6, label = kappa_string, size=7)

  ## Can get different colors, but if you build up the plot line by line, you won't get automatic centering.
  # p+annotate("text",x=max_x*.75, y=3, hjust = 0, parse=T, label='"Learning efficiency (\u03ba):"', color="black") +
    # annotate("text", x =  max_x*.75, y=2.8, hjust = 0, parse=T, label='"Pontiac Firebird"', color="green")
  
  print(length(plots))
  plots[[k]] = p
  
  newdir=paste(getwd(),'/plots/learning_curves/max=', max_x/1000, 'k/', sep='')
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=8, height=6)
}


plots_10k_with_rainbow = plots
layout = matrix(c(1:90), ncol=6, byrow=TRUE)
m = multiplot(plotlist = plots_10k_with_rainbow, layout=layout)
## save 50x30


## Human-normed figure (figure 3)
main_plot_agent_types = c('DDQN 100k', 'EMPA')
s = filter(human_normed_data, agent_type=='EMPA')
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$formatted_game_name
p = ggplot()+
  geom_bar(data=filter(human_normed_data, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(human_normed_composite_ratio, 10)>-3),
           aes(x=formatted_game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=filter(human_normed_data, agent_type%in%main_plot_agent_types & ((agent_type != 'DDQN 100k'  & !(log(human_normed_composite_ratio, 10)>-3)) | agent_type=='DDQN 100k')),
             aes(x=formatted_game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none',panel.background = element_blank())+
  ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c("EMPA", "DDQN 100k"),
                      labels=c("EMPA", "DDQN")) + scale_color_manual(values=colors,name="Model",
                                                                                         breaks=c("EMPA", "DDQN 100k"),
                                                                                         labels=c("EMPA", "DDQN"))
## 14x10


## Facet-wrapped plot that shows quartiles (Figure 4)
agents = c('EMPA', 'e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k','rainbow 150k', 'no goal gradient', 'no subgoals + no gradient', 'no IW', 'no subgoals', 'no subgoals + no gradient + no IW')
datapoints = data.frame(x1=as.numeric(), x2=as.numeric(), x3=as.numeric(), x4=as.numeric(), x5=as.numeric(), 
                        y1=as.numeric(), y2=as.numeric(), y3=as.numeric(), mean_val=as.numeric(), agent_type=as.character(), model_cluster=as.character())
for (i in 1:length(agents)){
  agent = agents[i]
  quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio), c(.1, .25, .5, .75, .9))
  mn=mean(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
  q1=quantiles[1]
  q2=quantiles[2]
  q3=quantiles[3]
  q4=quantiles[4]
  q5=quantiles[5]
  if (agent == 'EMPA'){
    m_cluster = 'EMPA'
  }
  if (agent %in% c('e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k')){
    m_cluster = 'Exploration ablations'
  }
  if (agent%in% c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                  'no IW', 'no subgoals + no gradient + no IW')){
    m_cluster = 'Planner ablations'
  }
  if (agent %in% c('DDQN 1k', 'DDQN 10k', 'DDQN 100k')){
      m_cluster = 'Deep RL'
  }
  if(grepl('rainbow', agent)){
    m_cluster = 'Deep RL'
  }
  if(agent=='random'){
    m_cluster = 'random'
  }
  

  y1=.875
  y2=.9
  y3=.925
  ## offsets for planner lesions
  if(agent=='no subgoals'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='no subgoals + no gradient'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  if(agent=='no IW'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  if(agent=='no subgoals + no gradient + no IW'){
    y1 = y1-.24
    y2 = y2-.24
    y3 = y3-.24
  }
  
  ## offsets for exploration lesions
  if(agent=='e-greedy 1k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='e-greedy 2k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  if(agent=='e-greedy 1k DS'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  if(agent=='e-greedy 2k DS'){
    y1 = y1-.24
    y2 = y2-.24
    y3 = y3-.24
  }
  
  ##offsets for DDQN
  if(agent=='DDQN 10k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='DDQN 100k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  
  ##offsets for rainbow
  if(agent=='rainbow 150k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='rainbow 250k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  
  datapoints = rbind(datapoints, data.frame(x1=q1, x2=q2, x3=q3, x4=q4, x5=q5,y1=y1, y2=y2, y3=y3, mean_val=mn, agent_type=agent,model_cluster=m_cluster))
  }


df = filter(human_normed_data, agent%in%agents, !is.na(model_cluster))
df = transform(df, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy 1k', 'e-greedy 2k', 'e-greedy 1k DS', 'e-greedy 2k DS',
                                                          'no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW',
                                                          'no subgoals + no gradient + no IW', 'DDQN 1k', 'DDQN 10k', 'DDQN 100k',
                                                          'rainbow 150k')))


datapoints = filter(datapoints, model_cluster%in%c('EMPA', 'Exploration ablations', 'Planner ablations', 'Deep RL'))
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)',10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
p = ggplot(df, aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed Efficiency") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.8)+
  geom_point(aes(x=mean_val, y=y2), shape=18, data=datapoints, size=7)+
  geom_segment(aes(x=x1, y=y2, xend=x2, yend=y2), linetype='longdash', data=datapoints, size=1.2)+ ##5-25
  geom_segment(aes(x=x2, y=y2, xend=x4, yend=y2), data=datapoints, size=1.2)+ ##25-75
  geom_segment(aes(x=x2, y=y1, xend=x2, yend=y3), data=datapoints, size=1.2)+ ##25 edge
  geom_segment(aes(x=x4, y=y1, xend=x4, yend=y3), data=datapoints, size=1.2)+ ## 75 edge
  geom_segment(aes(x=x4, y=y2, xend=x5, yend=y2), linetype='longdash', data=datapoints, size=1.2)+ ##75-95
  geom_segment(aes(x=x3, y=y1, xend=x3, yend=y3), data=datapoints, size=1.2)+ ##median line
  
      theme(legend.title=element_blank(), text=element_text(size=38), #legend.position='none',
            axis.text.x=element_text(size=34), axis.text.y=element_text(size=34), strip.text.x=element_text(size=44))+
  scale_x_continuous(breaks=logtickmarks,labels=tickmarks, limits=c(logtickmarks[1], 7.5)) +
  scale_y_continuous(limits=c(0,.95), breaks=c(0,.2,.4,.6,.8), labels=c(0,.2,.4,.6,.8))+
  facet_wrap(~model_cluster, ncol=1)
p
## 30x18


## Quick check on human-to-DQN performance
filter(human_normed_data, agent_type=='EMPA', (human_normed_composite_ratio>10 | human_normed_composite_ratio<.1))
filter(human_normed_data, agent_type=='DDQN 100k', human_normed_composite_ratio<.01)

## Plot subjective game ratings
s = summarySE(ratings, measurevar="difficulty", groupvars=c("source_game_name","variant_number"), na.rm=TRUE)
p = ggplot(s, aes(x=reorder(variant_number, as.numeric(variant_number)), y=difficulty)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=difficulty-ci, ymax=difficulty+ci))+
  facet_wrap(~source_game_name, ncol=3)+xlab('Game variant')+ylab('Difficulty')+scale_x_discrete(breaks=c(0,1,2,3,4),labels=c('original',1,2,3,4))
p  
##save 12x6

s = summarySE(ratings, measurevar="interestingness", groupvars=c("source_game_name","variant_number"), na.rm=TRUE)
p = ggplot(s, aes(x=reorder(variant_number, as.numeric(variant_number)), y=interestingness)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=interestingness-ci, ymax=interestingness+ci))+
  facet_wrap(~source_game_name, ncol=3)+xlab('Game variant')+ylab('Interestingness') +scale_x_discrete(breaks=c(0,1,2,3,4),labels=c('original',1,2,3,4))
p  
##save 12x6





## attempt to produce individual plots with quartiles.
# plots = list()
# i=1
# agents = c('EMPA', 'e-greedy .1', 'DDQN 100k')
# for (i in 1:length(agents)){
#   agent = agents[i]
#   ## Trying to just add the boxplot data manually
#   quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
#   print(agent)
#   print (i)
# 
#   q1=quantiles[2]
#   q2=quantiles[3]
#   q3=quantiles[4]
#   datapoints = data.frame(x=c(q1,q3), y=c(1.2, 1.2), agent_type=agent)
#   print(datapoints)
#   p = ggplot(filter(human_normed_data, agent_type==agent), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
#     geom_density(alpha=.8, adjust= 1/10)+
#     scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
#     geom_vline(xintercept=0,linetype='dashed',size=.4)+
#     geom_segment(aes(x=datapoints[1,]$x, y=datapoints[1,]$y, xend=datapoints[2,]$x, yend=datapoints[2,]$y), size=2, data=datapoints)+
#     theme(legend.title=element_blank())+scale_x_continuous(breaks=logtickmarks,labels=tickmarks, limits=c(logtickmarks[1], 6))
#     #+facet_wrap(~model_cluster, ncol=1)
#   p
#   newdir='~/Projects/atari/vgdl/plots/densities/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, agent, '.png', sep='')
#   ggsave(title, plot=p, width=7, height=3)
#   # i = i+1
# }

# layout = matrix(c(1:length(plots)), nrow=length(plots))
# m = multiplot(plotlist = plots, layout=layout)
# 8x10

## one plot per game summary plot of overall results -- easy to look at.
p = ggplot(subset(human_normed_data), aes(x=agent_type, y=level_percentage, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+facet_wrap(~game_name)+scale_fill_manual(values=colors)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+theme(legend.position='bottom')
p
## save as 10x16


p = ggplot(agentdata, aes(x=cumulative_steps, y=cumulative_wins, color=subject_ID))+geom_point()+geom_smooth()
p

## looks like 10 subjects won zelda, the rest did far worse (0,1, or 2 levels). Be careful how you average.
### you first need to generate cumulative wins
###level1-level2 plots
level_win_saved = level_win
level_win_proportions = level_win
d = filter(alldata, agent_type%in%c('human', 'EMPA', 'DDQN 100k', 'e-greedy .1'))

make_level_win_data = function(d){
  level_win = data.frame(agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$agent_type)){
      agentdata = filter(s, agent_type==agent)
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps - prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            subject_steps_to_win = level_steps
            # subject_steps_to_win = 1
          }
          else{
            subject_steps_to_win = no_win_equivalent_steps
            # subject_steps_to_win = 0
          }
          row = data.frame(agent_type=agent, subject_ID=subject, game_name=game, level_num=l, steps=subject_steps_to_win)
          level_win=rbind(level_win, row)
        }
      }
    }
  }
  level_win = transform(level_win, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy .1', "DDQN 100k"))) ## so that columns of plot are reordered
  return(level_win)
}


make_level_win_proportions = function(d){
  level_win = data.frame(agent_type=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$agent_type)){
      agentdata = filter(s, agent_type==agent)

      across_subjects = c()
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps - prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            # subject_steps_to_win = c(subject_steps_to_win, level_steps)
            subject_steps_to_win = c(subject_steps_to_win, 1)
          }
          else{
            # subject_steps_to_win = c(subject_steps_to_win, no_win_equivalent_steps)
            subject_steps_to_win = c(subject_steps_to_win, 0)

          }
        }
        across_subjects = rbind(across_subjects, subject_steps_to_win)
      }
      across_subjects  = colMeans(across_subjects)
      for (l in levels_to_try){
        row = data.frame(agent_type=agent, game_name=game, level_num=l, steps=across_subjects[l])
        level_win=rbind(level_win, row)

      }
    }
  }
  level_win = transform(level_win, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy .1', "DDQN 100k"))) ## so that columns of plot are reordered
  return(level_win)
}

level_win_proportions = make_level_win_proportions(d)

##Plot of steps to win level 1, conditioned on winning level 0. Only for games where the model *did* win level 1.
##Only the DDQN failed to win level 1
tmpcolors = c('palegreen3','steelblue3','slateblue2','grey50')
names(tmpcolors) = c('human', 'EMPA','e-greedy .1', 'DDQN 100k')

# p = ggplot(subset(level_win, level_num==1&steps!=-Inf), aes(x=short_agent_type, y=log(steps,10), fill=short_agent_type))
# p=p+geom_bar(position='dodge', stat='summary', fun.y='mean')+theme(legend.position='none')+scale_fill_manual(values=colors)
# p


# level_win_no_inf[level_win_no_inf$steps==10e15,]$steps=10e8

tickmarks = c(1,10e0,10e1,10e2,10e3,10e4,10e5,10e6,10e7,10e8,10e9,10e10,10e11,10e12,10e13,10e14,10e15)
logtickmarks=(log(tickmarks,10))

level_win = transform(level_win, agent_type=factor(agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')))

## all levels
p = ggplot(level_win, aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+scale_color_manual(values=tmpcolors)+
  scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+facet_wrap(~level_num, ncol=1)
p


## levels 1, 2
p = ggplot(filter(level_win_old, level_num%in%c(1,2)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+scale_color_manual(values=tmpcolors)+
  scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+facet_wrap(~level_num, ncol=1)
p

## Individual plots for steps to level 1, steps to level 2...
p = ggplot(filter(level_win, level_num%in%c(1)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  
    scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_linetype_manual(values=c(1,2,3,4,5))
p

## Individual plots for steps to level 1, steps to level 2...
p = ggplot(filter(level_win,level_num%in%c(2)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==2)$steps,10), na.rm=TRUE), linetype='l'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==2)$steps,10), na.rm=TRUE), linetype='k'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==2)$steps,10), na.rm=TRUE), linetype='j'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==2)$steps,10), na.rm=TRUE), linetype='i'))+
  
  scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p

p = ggplot(filter(level_win,level_num%in%c(3)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==3)$steps,10), na.rm=TRUE), linetype='l'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==3)$steps,10), na.rm=TRUE), linetype='k'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==3)$steps,10), na.rm=TRUE), linetype='j'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==3)$steps,10), na.rm=TRUE), linetype='i'))+
  
  scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p



p = ggplot(level_win_proportions, aes(x=level_num, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='summary',fun.y='mean', position='dodge')+
  scale_fill_manual(values=tmpcolors)+facet_wrap(~agent_type, nrow=1)
p=p+ylab('Proportion')+ggtitle('Level completion across games')+xlab("Level number")
p


p = ggplot(level_win_proportions, aes(x=game_name, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='identity', position='dodge')+
  scale_fill_manual(values=tmpcolors)+facet_wrap(~level_num, ncol=1) #facet_grid(level_num~game_name)#
p=p+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Proportion of agents to complete level')
p


for (game in unique(level_win_proportions$game_name)){
  p = ggplot(filter(level_win_proportions, game_name==game), aes(x=agent_type, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='identity', position='dodge')+
    scale_fill_manual(values=tmpcolors)+facet_wrap(~level_num, ncol=1) #facet_grid(level_num~game_name)#
  p=p+ggtitle(game)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Proportion of agents to complete level')
  
  newdir='~/Projects/atari/vgdl/interaction_plots/agent_win_proportions/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=4, height=6)
  
}


# complete_games = c()
# overcomplete_games = c()
# for (game in unique(EMPA_data$game_name)){
#   l = length(unique(filter(EMPA_data, game_name==game)$subject_ID))
#   if (l!=10){
#     overcomplete_games = c(overcomplete_games, game)
#   }else{
#     complete_games = c(complete_games, game)
#   }
# }

# for (game in complete_games){
#   p = ggplot(filter(EMPA_data, game_name==game), aes(x=cumulative_timestep, y=cumulative_wins, color=subject_ID))
#   p = p+geom_point()+geom_smooth()
#   # p
#   newdir='~/Projects/atari/vgdl/empa_plots/by_subject/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, game, '.png', sep='')
#   ggsave(title, plot=p, width=7, height=5) 
# }

### Planner lesion plot

## Standard boxplots
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p = ggplot(filter(human_normed_data, model_cluster%in%c('EMPA', 'planner lesions'))) + 
  geom_boxplot(aes(x=agent_type, y=log(human_normed_composite_ratio), fill=agent_type), outlier.shape=NA)+ # outlier.shape=NA removes outliers
  scale_color_manual(values=colors)+scale_fill_manual(values=colors)+
  scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p

## Facet-wrapped plot that shows quartiles!
agents = c('EMPA', 'e-greedy .1', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'no goal gradient', 'no subgoals + no gradient', 'no IW', 'no subgoals', 'no subgoals + no gradient + no IW')
boxplot_datapoints = data.frame(x1=as.numeric(), x2=as.numeric(), x3=as.numeric(), x4=as.numeric(), x5=as.numeric(), 
                        y1=as.numeric(), y2=as.numeric(), y3=as.numeric(), mean_val=as.numeric(), agent_type=as.character(), model_cluster=as.character())
for (i in 1:length(agents)){
  agent = agents[i]
  ## Trying to just add the boxplot data manually
  quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio), c(.1, .25, .5, .75, .9))
  mn=mean(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
  # q1=quantiles[2]
  # q2=quantiles[3]
  # q3=quantiles[4]
  q1=quantiles[1]
  q2=quantiles[2]
  q3=quantiles[3]
  q4=quantiles[4]
  q5=quantiles[5]
  if (agent == 'EMPA'){
    m_cluster = 'EMPA'
  }
  if (agent %in% c('e-greedy .1')){
    m_cluster = 'exploration lesions'
  }
  if (agent%in% c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                  'no IW', 'no subgoals + no gradient + no IW')){
    m_cluster = 'planner lesions'
  }
  if (agent %in% c('DDQN 1k', 'DDQN 10k', 'DDQN 100k')){
    m_cluster = 'DDQN'
  }
  
  y1=.9
  y2=1
  y3=1.1
  ## offsets for planner lesions
  if(agent=='no subgoals'){
    y1 = y1-.5
    y2 = y2-.5
    y3 = y3-.5
  }
    if(agent=='no goal gradient'){
    y1 = y1-1
    y2 = y2-1
    y3 = y3-1
  }
  if(agent=='no subgoals + no gradient'){
    y1 = y1-1.5
    y2 = y2-1.5
    y3 = y3-1.5
  }
  if(agent=='no IW'){
    y1 = y1-2
    y2 = y2-2
    y3 = y3-2
  }
  if(agent=='no subgoals + no gradient + no IW'){
    y1 = y1-2.5
    y2 = y2-2.5
    y3 = y3-2.5
  }
  
  ##add offsets for e-greedy before making plot

  ##offsets for DDQN
  if(agent=='DDQN 10k'){
    y1 = y1-3
    y2 = y2-3
    y3 = y3-3
  }
  if(agent=='DDQN 1k'){
    y1 = y1-3.5
    y2 = y2-3.5
    y3 = y3-3.5
  }
  
  boxplot_datapoints = rbind(boxplot_datapoints, data.frame(x1=q1, x2=q2, x3=q3, x4=q4, x5=q5,y1=y1, y2=y2, y3=y3, mean_val=mn, agent_type=agent,model_cluster=m_cluster))
}



data_to_plot = filter(boxplot_datapoints, model_cluster%in%c('EMPA', 'planner lesions'))
p = ggplot(data_to_plot, aes(color=agent_type)) + 
  geom_segment(aes(x=y2,y=x1,xend=y2,yend=x2), data=data_to_plot, linetype='dashed')+ ##10-25
  geom_segment(aes(x=y2,y=x4,xend=y2,yend=x5), data=data_to_plot, linetype='dashed')+ ##75-90
  
    # geom_segment(aes(x=y2,y=x2,xend=y2,yend=x4), data=data_to_plot)+ ##25+75. just use this is you want a single line 
  geom_segment(aes(x=y1,y=x2,xend=y1,yend=x4), data=data_to_plot)+ ##25+75. vertical edge
  geom_segment(aes(x=y3,y=x2,xend=y3,yend=x4), data=data_to_plot)+ ##25+75. vertical edge
  geom_segment(aes(x=y1,y=x2,xend=y3,yend=x2), data=data_to_plot)+ ##25+75. horizontal edge
  geom_segment(aes(x=y1,y=x4,xend=y3,yend=x4), data=data_to_plot)+ ##25+75. horizontal edge
  geom_point(aes(y=mean_val, x=y2), shape=5, data=data_to_plot)+ ##mean
  geom_segment(aes(x=y1,y=x3,xend=y3,yend=x3), data=data_to_plot)+
  scale_y_continuous(breaks=logtickmarks,labels=tickmarks)+
  ylab('Human-normed composite ratio')+xlab('Agent type')+ theme(axis.text.x = element_blank(), axis.ticks = element_blank())+
  scale_color_manual(values=colors)
p



eg = filter(alldata, agent_type=='e+greedy .1')
df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(), level_number=as.numeric(),
                cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric(), subsample_ID=as.character())
for (i in 1:10){
  tmp_df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(), level_number=as.numeric(),
                  cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
  subjects_to_sample = sample(unique(eg$subject_ID), 3, replace = FALSE, prob = NULL)
  subsample = filter(eg, subject_ID%in%subjects_to_sample)
  tmp_df = rbind(tmp_df, subsample)
  tmp_df$subsample_ID = i
  df = rbind(df, tmp_df)
}


make_level_win_for_subsamples = function(d){
  lw = data.frame(subsample_ID=as.character(), subject_ID=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$subsample_ID)){
      agentdata = filter(s, subsample_ID==agent)
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps + prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            subject_steps_to_win = level_steps
            # subject_steps_to_win = 1
          }
          else{
            subject_steps_to_win = no_win_equivalent_steps
            # subject_steps_to_win = 0
          }
          row = data.frame(subsample_ID=agent, subject_ID=subject, game_name=game, level_num=l, steps=subject_steps_to_win)
          lw=rbind(lw, row)
        }
      }
    }
  }
  return(lw)
}
lw=make_level_win_for_subsamples(df)
head(lw)

lw$subsample_ID=as.factor(lw$subsample_ID)
p = ggplot(filter(lw,level_num%in%c(1)), aes(x=log(steps,10), color=subsample_ID, fill=subsample_ID))
p = p+geom_density(alpha=.8, adjust=1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p

### You should actually make a plantimeata figure if what you're trying to check is what e+greedy would look like there if not sampled enough times.

human_df=filter(alldata, agent_type=='human')
head(human_df)
df$agent_type=df$subsample_ID
df = select(df, +subsample_ID)
df=rbind(df, human_df)
human_normed_df = make_human_normed_data(df)

           

